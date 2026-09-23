import pathlib,os,json,time,shutil,hashlib,random
from io_utils import sha,save,File
P=pathlib.Path(__file__).resolve().parent;OLD=P.parent/'single_carrier_introduction_v1';BASE=P.parent/'private_memory_competition_v1'
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 files={}
 for source in (OLD,BASE):
  for manifest in ('SOURCE_SHA256SUMS','INPUT_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
   for line in (source/manifest).read_text().splitlines():h,n=line.split(None,1);assert sha(source/n)==h;files['../'+source.name+'/'+n]=h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return files

def seed(b,r):return int(hashlib.sha256(('ORG-NOVELTY-045-r1|fresh_probe|%d|%d'%(b,r)).encode()).hexdigest()[:16],16)
def masks(rng):return [[rng.getrandbits(32) for i in range(32)] for g in range(40)]

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();rs=[dict(block=b,replicate=r,seed=seed(b,r),namespace='ORG-NOVELTY-045-r1|fresh_probe|%d|%d'%(b,r)) for b in range(24) for r in range(8)];numbers=[r['seed'] for r in rs];prior=set(json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers']);prior.update(x['seed'] for x in json.loads((BASE/'SEEDS.json').read_text()));assert len(numbers)==len(set(numbers))==192 and not set(numbers)&prior
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=192,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs)
 with File('fresh_probe_masks.jsonl.gz','w') as out:
  for r in rs:out.write(dict(block=r['block'],replicate=r['replicate'],fresh=masks(random.Random(r['seed']))))
 save('INPUT_REFERENCES.json',dict(files=refs,reused_old_paths=1536,new_paths=768,all_four_old_manifests_verified=True));shutil.copyfile(str(OLD/'BOOTSTRAP_INDICES.json'),'BOOTSTRAP_INDICES.json');save('INPUT_GENERATION.json',dict(new_seed_records=192,getrandbits32_calls=245760,stored_fresh_masks=245760,shared_across_both_costs_and_laws=True,other_new_draws=0,underlying_PRNG_word_count='implementation-dependent; not claimed'))
 files=['SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_REFERENCES.json','fresh_probe_masks.jsonl.gz','BOOTSTRAP_INDICES.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,input_manifest_sha256=sha('INPUT_SHA256SUMS'),source_manifest_sha256=sha('SOURCE_SHA256SUMS')))
if __name__=='__main__':main()
