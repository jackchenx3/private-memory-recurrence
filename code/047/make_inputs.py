import os,pathlib,json,time,hashlib,random
from io_utils import save,sha,File
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'independent_rare_memory_novelty_v1'

def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 files={}
 for source in (SOURCE,P.parent/'single_carrier_fresh_probe_v1',P.parent/'single_carrier_introduction_v1',P.parent/'private_memory_competition_v1'):
  for manifest in ('SOURCE_SHA256SUMS','INPUT_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
   for line in (source/manifest).read_text().splitlines():h,n=line.split(None,1);assert sha(source/n)==h;files['../'+source.name+'/'+n]=h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return files

def seed(f,b,r):return int(hashlib.sha256(('ORG-RESIDENT-047-r1|%s|%d|%d'%(f,b,r)).encode()).hexdigest()[:16],16)
def local_masks(rng):
 out=[]
 for g in range(40):
  row=[]
  for i in range(32):
   mask=0
   for bit in range(32):
    if rng.randrange(32)==0:mask|=1<<bit
   row.append(mask)
  out.append(row)
 return out

def scouts(rng):return [[rng.getrandbits(32) for i in range(32)] for g in range(40)]
def ties(rng):return [[rng.random() for j in range(128)] for g in range(40)]
def labels(rng):a=list(range(32));rng.shuffle(a);return a
def bootstrap(rng):return [[rng.randrange(24) for b in range(24)] for r in range(2000)]
def target_rows(b,t,original_iid,original_recur):
 out=[]
 for law in ('IID','RECUR'):
  indices=list(range(40)) if law=='IID' else [i%2 for i in range(40)];a=list(t) if law=='IID' else [original_recur[i%2] for i in range(40)];previous=(original_iid if law=='IID' else original_recur)[-1];out.append(dict(block=b,targets=a,source_indices=indices,source='new047target_draws' if law=='IID' else 'accepted046original_recurrent_pair',actual_changes=[False]+[a[i]!=a[i-1] for i in range(1,40)],boundary_change_from_preparation=a[0]!=previous,first_actual_change_convention='False at new initial measurement; boundary recorded separately',distinct_targets=len(set(a))))
 return out

def extract_states():
 n=0
 with File('RESIDENT_STATES.jsonl.gz','w') as out:
  for b in range(24):
   path=SOURCE/('raw/block%02d.jsonl.gz'%b);h=sha(path)
   with File(path,'r') as src:
    for row in src:
     if row['policy']!='SHAM_C0':continue
     r=row['record'];pop=r['populations'][-1];assert len(pop)==32;out.write(dict(block=b,replicate=row['replicate'],geometry=row['geometry'],genotypes=[q[0] for q in pop],source_population=pop,source_endpoint_frequency=r['frequencies'][-1],source_policy=row['policy'],source_path='../'+SOURCE.name+'/raw/'+path.name,source_sha256=h,source_update=40,new_founders='reset to positions0..31',source_query_count=r['query_counts']['total']));n+=1
 assert n==384
 save('RESIDENT_PROVENANCE.json',dict(status='PASS',source_states=n,source_paths_rerun=0,all_states_included=True,outcome_filtering=False,source_previously_incurred_calls=1978368,new_preparation_calls=0,new_founder_ids='ordered positions0..31',carrier_cache='own current genotype, update0, sampled position'))


def roster():
 coords=[('targets',b,-1) for b in range(24)]+[(f,b,r) for f in ('local','scout','ties','labels','fresh_probe') for b in range(24) for r in range(8)]+[('bootstrap',-1,-1)]
 return [dict(family=f,block=b,replicate=r,seed=seed(f,b,r),namespace='ORG-RESIDENT-047-r1|%s|%d|%d'%(f,b,r)) for f,b,r in coords]

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();save('INPUT_REFERENCES.json',dict(files=refs,old_population_inputs_used='384sourceendpointgenotypearrays only',old_trajectories_rerun=False));rs=roster();numbers=[q['seed'] for q in rs];prior=set(json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers']);assert len(numbers)==len(set(numbers))==985;assert not set(numbers)&prior
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=985,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs);extract_states();original={g:json.loads((SOURCE/(g+'_TARGETS.json')).read_text())['blocks'] for g in ('IID','RECUR')};candidate=[];iid=[];recur=[]
 for b in range(24):
  rng=random.Random(seed('targets',b,-1));t=[rng.getrandbits(32) for i in range(40)];candidate.append(dict(block=b,targets=t));a,z=target_rows(b,t,original['IID'][b]['targets'],original['RECUR'][b]['targets']);iid.append(a);recur.append(z)
 save('TARGETS.json',dict(blocks=candidate));save('IID_TARGETS.json',dict(blocks=iid));save('RECUR_TARGETS.json',dict(blocks=recur))
 with File('streams.jsonl.gz','w') as out,File('fresh_probe_masks.jsonl.gz','w') as freshout:
  for b in range(24):
   for r in range(8):
    freshout.write(dict(block=b,replicate=r,fresh=scouts(random.Random(seed('fresh_probe',b,r)))))
    out.write(dict(block=b,replicate=r,draws=dict(local=local_masks(random.Random(seed('local',b,r))),scout=scouts(random.Random(seed('scout',b,r))),ties=ties(random.Random(seed('ties',b,r))),labels=labels(random.Random(seed('labels',b,r))))))
 save('BOOTSTRAP_INDICES.json',bootstrap(random.Random(seed('bootstrap',-1,-1))));save('INPUT_GENERATION.json',dict(seed_records=985,target_getrandbits32=960,local_masks=245760,local_randrange32=7864320,scout_getrandbits32=245760,fresh_probe_getrandbits32=245760,tie_random_calls=983040,label_shuffles=192,bootstrap_randrange24=48000,underlying_PRNG_word_count='implementation-dependent; not claimed',old_inputs_used='384residentstates and recurrent pair only'))
 files=['RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','INPUT_REFERENCES.json','fresh_probe_masks.jsonl.gz','SEEDS.json','SEED_COLLISION_CHECK.json','TARGETS.json','IID_TARGETS.json','RECUR_TARGETS.json','streams.jsonl.gz','BOOTSTRAP_INDICES.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
