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
 assert len(values)==2808 and sum(structural(k) for k in values)==228
 (P/'summary.json').write_text(json.dumps(dict(primary='RACE32|HALF|ACTIVE_C0-NOVEL_C0|D40',values=values,interval_scope='Known047preparedRECURcohort;3456newRACE32and3456storedBEST32controls;192survivalseeds;unchanged2000wholeblockbootstrap;all intervals including primary approximate pointwise',numpy_version=np.__version__,python=sys.version),indent=2)+'\n')
 (P/'INFERENCE_CHECK.json').write_text(json.dumps(dict(status='PASS',records=2808,structural_zero_records=228,numpy_version=np.__version__,quantile_method='linear',analysis_location='local postallocation; stored outputs only',new_dynamics=0),indent=2)+'\n')
 old=json.loads((P.parent/'intermittent_private_memory_v1/summary.json').read_text())['values'];baseline=[k for k in values if k.split('|')[0]=='BEST32'];assert len(baseline)==1248
 for k in baseline:
  ref=old[k.replace('BEST32|','RESIDENT40|')]
  for field in ('mean','ci95','zero_classification'):assert values[k][field]==ref[field],(k,field)
 (P/'BASELINE_REUSE_CHECK.json').write_text(json.dumps(dict(status='PASS',exact_interval_records=1248,stored_control_paths=3456,controls_rerun=0,comparison_fields=['mean','ci95','zero_classification']),indent=2)+'\n')
 print(values['RACE32|HALF|ACTIVE_C0-NOVEL_C0|D40'])
if __name__=='__main__':main()
