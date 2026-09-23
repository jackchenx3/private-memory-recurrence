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
 oldcols={}
 for row in json.loads((P/'OLD_BASE_BLOCKS.json').read_text()):
  v=row['values']
  for g in LAWS:
   for c in COSTS:
    for m in RAW+FREQ:v['RACE32|'+g+'|ACTIVE_'+c+'-NOVEL_'+c+'|'+m]=v['RACE32|'+g+'|ACTIVE_'+c+'|'+m]-v['RACE32|'+g+'|NOVEL_'+c+'|'+m]
  for k,x in v.items():oldcols.setdefault(k,[]).append(x)
 old=json.loads((P.parent/'probabilistic_private_memory_v1/summary.json').read_text())['values'];exact={}
 for k,x in oldcols.items():
  a=np.asarray(x);ci=np.quantile(a[idx].mean(axis=1),[.025,.975],method='linear').tolist();m=k.split('|')[-1];contrast='-' in k.split('|')[2];cl='structural_zero' if contrast and m in ('U0','F0') else 'observed_exact_zero' if np.all(a==0) else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved';q=dict(mean=float(a.mean()),ci95=ci,zero_classification=cl);assert all(q[f]==old[k][f] for f in q),(k,q,old[k]);exact[k]=q
 assert len(exact)==468;save('OLD_FIRST_POSITION_INTERVALS.json',exact);save('BASELINE_REUSE_CHECK.json',dict(status='PASS',exact_interval_records=468,stored_control_paths=2304,controls_rerun=0,part_of_new_inference_grid=False));print(values['HALF|C0|MIX_H_MINUS_F|D40'])
if __name__=='__main__':main()
