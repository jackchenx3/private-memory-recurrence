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


def seed(b,r):return int(hashlib.sha256(('ORG-DIRECTION-048-r1|probe_direction|%d|%d'%(b,r)).encode()).hexdigest()[:16],16)
def roster():return [dict(family='probe_direction',block=b,replicate=r,seed=seed(b,r),namespace='ORG-DIRECTION-048-r1|probe_direction|%d|%d'%(b,r)) for b in range(24) for r in range(8)]
def permutations(rng):
 out=[]
 for g in range(40):
  row=[]
  for i in range(32):
   a=list(range(32));rng.shuffle(a);row.append(a)
  out.append(row)
 return out

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();save('INPUT_REFERENCES.json',dict(files=refs,old_control_paths=4608,controls_rerun=0,source_resident_states=384));rs=roster();numbers=[q['seed'] for q in rs];prior=set(json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers']);assert len(numbers)==len(set(numbers))==192 and not set(numbers)&prior
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=192,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs)
 with File('probe_permutations.jsonl.gz','w') as out:
  for b in range(24):
   for r in range(8):out.write(dict(block=b,replicate=r,permutations=permutations(random.Random(seed(b,r)))))
 copied=['RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','TARGETS.json','IID_TARGETS.json','RECUR_TARGETS.json','streams.jsonl.gz','fresh_probe_masks.jsonl.gz','BOOTSTRAP_INDICES.json']
 for n in copied:shutil.copyfile(str(SOURCE/n),n);assert sha(n)==sha(SOURCE/n)
 save('INPUT_GENERATION.json',dict(seed_records=192,logical_permutation_shuffles=245760,permutation_length=32,draw_order='update-major/recipient-major, fresh list(range32) each slot',underlying_PRNG_word_count='implementation-dependent; not claimed',old_paths_reused=4608,new_other_random_inputs=0))
 files=copied+['INPUT_REFERENCES.json','probe_permutations.jsonl.gz','SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
