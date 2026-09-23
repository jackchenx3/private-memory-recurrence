import os,pathlib,json,time,hashlib,random
from io_utils import save,sha,File
P=pathlib.Path(__file__).resolve().parent

def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 files={}
 for source in (P.parent/'single_carrier_fresh_probe_v1',P.parent/'single_carrier_introduction_v1',P.parent/'private_memory_competition_v1'):
  for manifest in ('SOURCE_SHA256SUMS','INPUT_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
   for line in (source/manifest).read_text().splitlines():h,n=line.split(None,1);assert sha(source/n)==h;files['../'+source.name+'/'+n]=h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return files

def seed(f,b,r):return int(hashlib.sha256(('ORG-REGIMEREP-046-r1|%s|%d|%d'%(f,b,r)).encode()).hexdigest()[:16],16)
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
def target_rows(b,t):
 out=[]
 for g in ('IID','RECUR'):
  indices=list(range(40)) if g=='IID' else [i%2 for i in range(40)];a=[t[i] for i in indices];out.append(dict(block=b,targets=a,source_indices=indices,actual_changes=[False]+[a[i]!=a[i-1] for i in range(1,40)],distinct_targets=len(set(a))))
 return out

def roster():
 coords=[('targets',b,-1) for b in range(24)]+[(f,b,r) for f in ('local','scout','ties','labels','fresh_probe') for b in range(24) for r in range(8)]+[('bootstrap',-1,-1)]
 return [dict(family=f,block=b,replicate=r,seed=seed(f,b,r),namespace='ORG-REGIMEREP-046-r1|%s|%d|%d'%(f,b,r)) for f,b,r in coords]

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();save('INPUT_REFERENCES.json',dict(files=refs,old_population_inputs_used=False,accepted_code_only=True));rs=roster();numbers=[q['seed'] for q in rs];prior=set(json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers']);assert len(numbers)==len(set(numbers))==985;assert not set(numbers)&prior
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=985,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs);candidate=[];iid=[];recur=[]
 for b in range(24):
  rng=random.Random(seed('targets',b,-1));t=[rng.getrandbits(32) for i in range(40)];candidate.append(dict(block=b,targets=t));a,z=target_rows(b,t);iid.append(a);recur.append(z)
 save('TARGETS.json',dict(blocks=candidate));save('IID_TARGETS.json',dict(blocks=iid));save('RECUR_TARGETS.json',dict(blocks=recur))
 with File('streams.jsonl.gz','w') as out,File('fresh_probe_masks.jsonl.gz','w') as freshout:
  for b in range(24):
   for r in range(8):
    freshout.write(dict(block=b,replicate=r,fresh=scouts(random.Random(seed('fresh_probe',b,r)))))
    out.write(dict(block=b,replicate=r,draws=dict(local=local_masks(random.Random(seed('local',b,r))),scout=scouts(random.Random(seed('scout',b,r))),ties=ties(random.Random(seed('ties',b,r))),labels=labels(random.Random(seed('labels',b,r))))))
 save('BOOTSTRAP_INDICES.json',bootstrap(random.Random(seed('bootstrap',-1,-1))));save('INPUT_GENERATION.json',dict(seed_records=985,target_getrandbits32=960,local_masks=245760,local_randrange32=7864320,scout_getrandbits32=245760,fresh_probe_getrandbits32=245760,tie_random_calls=983040,label_shuffles=192,bootstrap_randrange24=48000,underlying_PRNG_word_count='implementation-dependent; not claimed',old_inputs_used=False))
 files=['INPUT_REFERENCES.json','fresh_probe_masks.jsonl.gz','SEEDS.json','SEED_COLLISION_CHECK.json','TARGETS.json','IID_TARGETS.json','RECUR_TARGETS.json','streams.jsonl.gz','BOOTSTRAP_INDICES.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
