import os,pathlib,json,time,hashlib,random,shutil
from io_utils import save,sha,File
from model import to_uniform
P=pathlib.Path(__file__).resolve().parent;SOURCE=P.parent/'intermittent_private_memory_v1'
def verify_inherited():
 for line in (P/'INHERITED_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);assert sha(P/n)==h
 files={}
 for source in (SOURCE,P.parent/'prepared_resident_introduction_v1',P.parent/'independent_rare_memory_novelty_v1',P.parent/'single_carrier_fresh_probe_v1',P.parent/'single_carrier_introduction_v1',P.parent/'private_memory_competition_v1'):
  for manifest in ('SOURCE_SHA256SUMS','INPUT_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
   for line in (source/manifest).read_text().splitlines():h,n=line.split(None,1);assert sha(source/n)==h;files['../'+source.name+'/'+n]=h
 for n,q in json.loads((P/'IMPLEMENTATION_MAP.json').read_text()).items():assert sha(P/n)==q['sha256']==sha(P/q['source'])
 return files




def seed(b,r):return int(hashlib.sha256(('ORG-SURVIVAL-050-r1|survival|%d|%d'%(b,r)).encode()).hexdigest()[:16],16)
def roster():return [dict(family='survival',block=b,replicate=r,seed=seed(b,r),namespace='ORG-SURVIVAL-050-r1|survival|%d|%d'%(b,r)) for b in range(24) for r in range(8)]
def draws(rng):
 out=[]
 for g in range(40):
  ks=[rng.getrandbits(52) for j in range(128)];out.append(dict(k=ks,u=[to_uniform(k) for k in ks]))
 return out

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('INPUT_FREEZE.json').exists();refs=verify_inherited();save('INPUT_REFERENCES.json',dict(files=refs,old_control_paths=3456,controls_rerun=0,source_resident_states=192,nested_FULL_reuse_from047=True));rs=json.loads(pathlib.Path('SEED_ROSTER.json').read_text());assert rs==roster();numbers=[q['seed'] for q in rs];prior=set(json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers']);assert len(numbers)==len(set(numbers))==192 and not set(numbers)&prior
 save('SEED_COLLISION_CHECK.json',dict(status='PASS',unique_new=192,prior_integer_inventory=len(prior),collision_count=0,checked_before_random_generation=True));save('SEEDS.json',rs)
 with File('survival_streams.jsonl.gz','w') as out:
  for b in range(24):
   for r in range(8):out.write(dict(block=b,replicate=r,survival=draws(random.Random(seed(b,r)))))
 copied=['streams.jsonl.gz','fresh_probe_masks.jsonl.gz','BOOTSTRAP_INDICES.json','RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','TARGET_LAW_DRAWS.json','ZERO_TARGETS.json','HALF_TARGETS.json','FULL_TARGETS.json']
 for n in copied:shutil.copyfile(str(SOURCE/n),n);assert sha(n)==sha(SOURCE/n)
 save('INPUT_GENERATION.json',dict(seed_records=192,survival_getrandbits52=983040,draw_order='update0..39 thencandidate0..127',uniform_conversion='(k+1)/(2**52+1)',underlying_PRNG_word_count='not claimed beyond APIcalls',old_paths_reused=3456,new_other_random_inputs=0))
 files=copied+['survival_streams.jsonl.gz','INPUT_REFERENCES.json','SEEDS.json','SEED_COLLISION_CHECK.json','INPUT_GENERATION.json'];hashes={n:sha(n) for n in files};pathlib.Path('INPUT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_manifest_sha256=sha('INPUT_SHA256SUMS')))
if __name__=='__main__':main()
