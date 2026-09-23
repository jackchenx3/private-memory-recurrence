"""Authenticate saved stage boundaries without scoring or propagation."""
import pathlib,json,gzip
from model import rebase,substitute
P=pathlib.Path(__file__).resolve().parent
def rows(name):
 with gzip.open(P/name,'rt') as src:
  for line in src:yield json.loads(line)
def load():
 states={(q['block'],q['replicate'],q['geometry'],q['background']):q for q in rows('RESIDENT_STATES.jsonl.gz')};labels={(q['block'],q['replicate']):q['draws']['labels'] for q in rows('streams.jsonl.gz')};fresh={(q['block'],q['replicate']):q['fresh'] for q in rows('fresh_probe_masks.jsonl.gz')};targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in ('ZERO','HALF','FULL')};assert len(states)==1152 and len(labels)==len(fresh)==192;return states,labels,fresh,targets

def check(row,loaded):
 states,labels,fresh,targets=loaded;b,r,g,bg,cfg=row['block'],row['replicate'],row['geometry'],row['background'],row['configuration'];state=states[b,r,g,bg];rec=row['record'];lab=labels[b,r];assert row['founder_ids']==lab[:2];pop,mapping=rebase(state['population']);assert mapping==state['founder_rebase_map']==row['preparation_founder_map'];slot=None if cfg.endswith('STAY') else lab[int(cfg[-1])];expected=substitute(pop,bg,slot);assert json.loads(json.dumps(expected))==rec['populations'][0];assert row['rare_founder_id']==slot;ts=targets[g][b];assert rec['absolute_start']==40 and rec['boundary_previous_target']==state['last_preparation_target'] and rec['boundary_current_target']==ts['targets'][0] and rec['boundary_actual_change']==ts['boundary_actual_change'];assert ts['preparation_terminal_targets']==state['last_two_preparation_targets']
 assert [q['genotype'] for q in rec['initial_queries']]==[q[0] for q in expected] and [q['raw_mismatch'] for q in rec['initial_queries']]==rec['initial_raw_mismatches'];assert rec['raw_losses'][0]==sum(rec['initial_raw_mismatches'])/1024
 for i,(st,truth) in enumerate(zip(rec['steps'],rec['ground_truth'])):
  assert st['fresh_probe_masks']==fresh[b,r][i];assert truth['target']==ts['targets'][i] and truth['absolute_update']==40+i;assert truth['actual_change']==(i>0 and ts['targets'][i]!=ts['targets'][i-1])
 return True
