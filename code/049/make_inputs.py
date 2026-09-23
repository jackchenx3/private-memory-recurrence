import os,pathlib,json,time,hashlib,random,shutil
from io_utils import save,sha,File
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'prepared_resident_introduction_v1'
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 files={}
 for source in (SOURCE,P.parent/'independent_rare_memory_novelty_v1',P.parent/'single_carrier_fresh_probe_v1',P.parent/'single_carrier_introduction_v1',P.parent/'private_memory_competition_v1'):
  for manifest in ('SOURCE_SHA256SUMS','INPUT_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
   for line in (source/manifest).read_text().splitlines():h,n=line.split(None,1);assert sha(source/n)==h;files['../'+source.name+'/'+n]=h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return files



def seed(f,b):return int(hashlib.sha256(('ORG-INTERMIT-049-r1|%s|%d'%(f,b)).encode()).hexdigest()[:16],16)
def roster():return [dict(family=f,block=b,seed=seed(f,b),namespace='ORG-INTERMIT-049-r1|%s|%d'%(f,b)) for f in ('innovations','copy') for b in range(24)]
def draws(rng,bits):return [rng.getrandbits(bits) for t in range(2,40)]
def build_targets(pair,innovations,copy,law):
 assert law in ('ZERO','HALF','FULL') and len(pair)==2 and len(innovations)==len(copy)==38 and all(c in (0,1) for c in copy)
 ts=list(pair)
 for j,z in enumerate(innovations):ts.append(ts[-2] if law=='FULL' or law=='HALF' and copy[j] else z)
 return ts

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();save('INPUT_REFERENCES.json',dict(files=refs,old_control_paths=1152,controls_rerun=0,source_resident_states=192,source_filter='RESIDENT40/RECUR only, every state included'))
 rs=roster();numbers=[q['seed'] for q in rs];prior=set(json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers']);assert len(numbers)==len(set(numbers))==48 and not set(numbers)&prior;save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=48,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs)
 full=json.loads((SOURCE/'RECUR_TARGETS.json').read_text())['blocks'];inputs=[];targets={g:[] for g in ('ZERO','HALF','FULL')}
 for b in range(24):
  z=draws(random.Random(seed('innovations',b)),32);cs=draws(random.Random(seed('copy',b)),1);pair=full[b]['targets'][:2];inputs.append(dict(block=b,first_pair=pair,innovations=z,copy_bits=cs,indices=list(range(2,40))))
  for g in targets:
   ts=build_targets(pair,z,cs,g);row=dict(block=b,targets=ts,actual_changes=[False]+[ts[j]!=ts[j-1] for j in range(1,40)],boundary_change_from_preparation=full[b]['boundary_change_from_preparation'],first_actual_change_convention=full[b]['first_actual_change_convention'],distinct_targets=len(set(ts)),law=g)
   if g=='FULL':assert ts==full[b]['targets']
   targets[g].append(row)
 save('TARGET_LAW_DRAWS.json',dict(blocks=inputs))
 for g,rows in targets.items():save(g+'_TARGETS.json',dict(blocks=rows))
 copied=['streams.jsonl.gz','fresh_probe_masks.jsonl.gz','BOOTSTRAP_INDICES.json']
 for n in copied:shutil.copyfile(str(SOURCE/n),n);assert sha(n)==sha(SOURCE/n)
 n=0
 with File(SOURCE/'RESIDENT_STATES.jsonl.gz','r') as src,File('RESIDENT_STATES.jsonl.gz','w') as out:
  for row in src:
   if row['geometry']=='RECUR':out.write(row);n+=1
 assert n==192
 save('RESIDENT_PROVENANCE.json',dict(status='PASS',source_states=192,source_paths_rerun=0,all_recurrent_states_included=True,outcome_filtering=False,source_previously_incurred_calls=989184,new_preparation_calls=0,new_founder_ids='reused047 reset positions0..31',carrier_cache='reused own current genotype, update0, sampled position'))
 save('INPUT_GENERATION.json',dict(seed_records=48,innovation_getrandbits32=912,copy_getrandbits1=912,draw_order='increasing t2..39 per independent family/block',underlying_PRNG_word_count='not claimed beyond APIcalls',old_paths_reused=1152,new_other_random_inputs=0))
 files=copied+['RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','TARGET_LAW_DRAWS.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json','INPUT_REFERENCES.json','SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
