"""Audit frozen prepared states and recorded computations; no new objective calls."""
import pathlib,json,gzip,math,struct,collections
from model import all_policy,rebase
from make_inputs import extend_targets
P=pathlib.Path(__file__).resolve().parent

def rows(name):
 with gzip.open(P/name,'rt') as src:
  for line in src:yield json.loads(line)
def ulp(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def main():
 source={(q['block'],q['replicate']):q['genotypes'] for q in rows('reused052_RESIDENT_STATES.jsonl.gz')};states={(q['block'],q['replicate'],q['geometry'],q['background']):q for q in rows('RESIDENT_STATES.jsonl.gz')};fresh={(q['block'],q['replicate']):q['fresh'] for q in rows('reused052_fresh_probe_masks.jsonl.gz')};targets={g:json.loads((P/('reused052_'+g+'_TARGETS.json')).read_text())['blocks'] for g in ('ZERO','HALF','FULL')};newtargets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in targets};draws=json.loads((P/'TARGET_LAW_DRAWS.json').read_text())['blocks'];n=clocks=nonexact=maxulp=0
 for g in targets:
  for b in range(24):assert extend_targets(targets[g][b]['targets'],draws[b]['innovations'],draws[b]['copy_bits'],g)==newtargets[g][b]['targets']
 assert len(source)==192 and len(states)==1152
 for b in range(24):
  for row in rows('preparation/block%02d.jsonl.gz'%b):
   r,g,bg=row['replicate'],row['geometry'],row['background'];rec=row['record'];state=states[b,r,g,bg];initial=all_policy(source[b,r],bg);assert json.loads(json.dumps(initial))==rec['populations'][0];assert rec['populations'][-1]==state['population'];rebased,mapping=rebase(state['population']);assert json.loads(json.dumps(rebased))==state['rebased_population'] and mapping==state['founder_rebase_map'];assert rec['absolute_start']==0 and rec['boundary_previous_target'] is None;assert rec['frequencies'][bg]==[1]*41 and rec['frequencies']['R']==[0]*41;ts=targets[g][b]['targets'];assert state['last_two_preparation_targets']==ts[-2:];assert rec['query_counts']['total']==5152
   assert rec['raw_losses']==rec['penalized_losses'];assert [q['genotype'] for q in rec['initial_queries']]==source[b,r];assert [q['raw_mismatch'] for q in rec['initial_queries']]==rec['initial_raw_mismatches']
   for j,st in enumerate(rec['steps']):
    before=rec['populations'][j];after=rec['populations'][j+1];assert st['evaluator_calls']==128 and len(st['candidates'])==128;assert st['selected_records']==after==[st['candidates'][i] for i in st['selected_indices']];assert sum(st['current_descendant_counts'])==32 and st['persistent_cache_count']==32;assert st['candidate_raw_mismatches']==st['candidate_penalized_mismatches'];assert st['fresh_probe_masks']==fresh[b,r][j];assert rec['ground_truth'][j]['target']==ts[j] and rec['ground_truth'][j]['absolute_update']==j;assert st['S_raw']==st['S_pen'];assert st['L_raw']==rec['raw_losses'][j+1];assert st['L_raw']-rec['raw_losses'][j]==st['W_raw']-st['S_raw']
    for i,q in enumerate(st['candidates']):assert q[1:3]==before[i%32][1:3];assert q[3]==(before[i][3] if i<32 else [before[i%32][0],j,i%32]);assert st['query_records'][i]['candidate_index']==i and st['query_records'][i]['genotype']==q[0] and st['query_records'][i]['raw_mismatch']==st['candidate_raw_mismatches'][i]
    for d in st['donor_choices']:assert d['winner_index']==min(d['candidate_indices'],key=lambda i:(st['candidate_raw_mismatches'][i],st['ties'][i],i))
    assert all(0<u<1 and u==(k+1)/(2**52+1) for k,u in zip(st['survival_integers'],st['survival_uniforms']));keys=[-math.log(u)*float(1<<s) for u,s in zip(st['survival_uniforms'],st['candidate_penalized_mismatches'])];ds=[ulp(x,y) for x,y in zip(keys,st['race_keys'])];assert max(ds)<=2;clocks+=128;nonexact+=sum(x>0 for x in ds);maxulp=max(maxulp,max(ds));assert st['selected_indices']==sorted(range(128),key=lambda i:(st['race_keys'][i],st['ties'][i],i))[:32]==sorted(range(128),key=lambda i:(keys[i],st['ties'][i],i))[:32]
   n+=1
 assert n==1152 and clocks==5898240;blocks=json.loads((P/'PREPARATION_BLOCK_SUMMARIES.json').read_text());assert len(blocks)==144 and all(q['paths']==8 for q in blocks);first=json.loads((P/'INPUT_FREEZE.json').read_text())['freeze_unix'];second=json.loads((P/'RESIDENT_FREEZE.json').read_text())['freeze_unix'];third=json.loads((P/'TRANSFER_STARTED.json').read_text())['start'];assert first<second<third
 (P/'PREPARATION_CHECK.json').write_text(json.dumps(dict(status='PASS',prepared_states=n,source_arrays=192,prepared_block_summaries=144,all_states_retained=True,cache_and_founder_rebase_maps_exact=True,continued_target_laws_exact=True,exogenous_then_endogenous_freeze_before_stages=True,saved_clock_checks=clocks,non_bitwise_identical=nonexact,maximum_ulp_difference=maxulp,tolerance_ulp=2,all_saved_and_recomputed_survivor_orders_exactly_equal=True,extra_objective_calls=0),indent=2)+'\n')
if __name__=='__main__':main()
